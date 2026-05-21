import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { createClient } from '@supabase/supabase-js';


const PLAN_BY_PRICE: Record<string, string> = {
  [process.env.STRIPE_STARTER_PRICE_ID ?? '']: 'starter',
  [process.env.STRIPE_PRO_PRICE_ID ?? '']: 'pro',
  [process.env.STRIPE_ELITE_PRICE_ID ?? '']: 'elite',
};

export async function POST(req: NextRequest) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '2026-04-22.dahlia' });
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
  const sig = req.headers.get('stripe-signature')!;
  const body = await req.text();

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object as Stripe.Checkout.Session;
    const userId = session.metadata?.user_id;
    const customerId = session.customer as string;
    const subscriptionId = session.subscription as string;

    if (!userId) return NextResponse.json({ ok: true });

    const subscription = await stripe.subscriptions.retrieve(subscriptionId);
    const priceId = subscription.items.data[0]?.price.id;
    const plan = PLAN_BY_PRICE[priceId] ?? 'starter';

    await supabase.from('users').update({
      stripe_customer_id: customerId,
      plan,
    }).eq('id', userId);

    await supabase.from('subscriptions').upsert({
      user_id: userId,
      stripe_subscription_id: subscriptionId,
      status: subscription.status,
      plan,
      current_period_end: new Date((subscription as unknown as { current_period_end: number }).current_period_end * 1000).toISOString(),
    }, { onConflict: 'stripe_subscription_id' });
  }

  if (event.type === 'customer.subscription.deleted') {
    const subscription = event.data.object as Stripe.Subscription;
    // Downgrade to trial on cancellation
    const { data: sub } = await supabase
      .from('subscriptions')
      .select('user_id')
      .eq('stripe_subscription_id', subscription.id)
      .single();

    if (sub?.user_id) {
      await supabase.from('users').update({ plan: 'trial' }).eq('id', sub.user_id);
      await supabase
        .from('subscriptions')
        .update({ status: 'canceled' })
        .eq('stripe_subscription_id', subscription.id);
    }
  }

  return NextResponse.json({ ok: true });
}
