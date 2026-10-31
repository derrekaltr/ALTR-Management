import type { AccountPacket, ReelPacket } from "../metrics/packet.js";
import type { AccountCritique, CritiqueRecord, ReelCritique } from "../critique/schemas.js";
import type { Dataset } from "../ingest/types.js";

export interface ReportBundle {
  generated_at: string;
  profile: string;
  account: Dataset["account"];
  account_packet: AccountPacket;
  account_critique: CritiqueRecord<AccountCritique> | null;
  reels: Array<{ packet: ReelPacket; critique: CritiqueRecord<ReelCritique> | null }>;
}

export function renderJson(bundle: ReportBundle): string {
  return JSON.stringify(bundle, null, 2) + "\n";
}
