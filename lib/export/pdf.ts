import { jsPDF } from 'jspdf';

interface ExportParams {
  player: Record<string, unknown>;
  content: Record<string, string>;
  audienceLabel: string;
  language: string;
}

const EMERALD = [16, 185, 129] as const;
const DARK    = [17, 24, 39] as const;
const GRAY    = [107, 114, 128] as const;
const WHITE   = [255, 255, 255] as const;
const LIGHT   = [243, 244, 246] as const;

export async function generatePDF({ player, content, audienceLabel, language }: ExportParams): Promise<Buffer> {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const W = 210;
  const MARGIN = 16;
  const contentW = W - MARGIN * 2;

  // --- Header bar ---
  doc.setFillColor(...DARK);
  doc.rect(0, 0, W, 32, 'F');

  doc.setTextColor(...EMERALD);
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('ScoutIQ', MARGIN, 14);

  doc.setTextColor(...GRAY);
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.text('Professional Football Scouting Intelligence', MARGIN, 20);

  doc.setTextColor(...WHITE);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text(`${audienceLabel} Report`, MARGIN, 28);

  // --- Player banner ---
  doc.setFillColor(...LIGHT);
  doc.rect(0, 32, W, 22, 'F');

  doc.setTextColor(...DARK);
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.text(String(player.name ?? ''), MARGIN, 42);

  doc.setTextColor(...GRAY);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  const subtitle = [player.position, player.current_club, player.league, player.age ? `Age ${player.age}` : null]
    .filter(Boolean).join(' · ');
  doc.text(subtitle, MARGIN, 49);

  // Language label top-right
  doc.setFontSize(8);
  doc.setTextColor(...EMERALD);
  doc.text(language.toUpperCase(), W - MARGIN, 42, { align: 'right' });

  // --- Content sections ---
  let y = 62;
  const lineH = 5.5;
  const sectionPad = 5;

  for (const [key, value] of Object.entries(content)) {
    if (!value) continue;

    // Section title
    doc.setFillColor(...EMERALD);
    doc.rect(MARGIN, y, 3, 6, 'F');
    doc.setTextColor(...DARK);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    const title = key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    doc.text(title, MARGIN + 6, y + 5);
    y += 10;

    // Section body
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(55, 65, 81);
    const lines = doc.splitTextToSize(String(value), contentW);
    for (const line of lines) {
      if (y > 272) {
        doc.addPage();
        y = MARGIN;
      }
      doc.text(line, MARGIN, y);
      y += lineH;
    }
    y += sectionPad;
  }

  // --- Footer ---
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFillColor(...DARK);
    doc.rect(0, 284, W, 13, 'F');
    doc.setTextColor(...GRAY);
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.text('ScoutIQ · scoutiq.app · AI-generated content uses only provided data.', MARGIN, 291);
    doc.text(`${i} / ${pageCount}`, W - MARGIN, 291, { align: 'right' });
  }

  return Buffer.from(doc.output('arraybuffer'));
}
