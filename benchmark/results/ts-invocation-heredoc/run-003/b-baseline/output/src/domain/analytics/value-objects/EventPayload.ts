/** Value object representing an event payload. */
export interface EventPayload {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
