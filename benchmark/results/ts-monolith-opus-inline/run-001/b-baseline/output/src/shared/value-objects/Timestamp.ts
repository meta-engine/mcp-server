/** Point-in-time value carrying both epoch seconds and ISO representation. */
export interface Timestamp {
  epochSeconds: number;
  iso: string;
}
