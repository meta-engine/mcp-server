/** Point-in-time value object with both epoch and ISO representations. */
export interface Timestamp {
  epochSeconds: number;
  iso: string;
}
