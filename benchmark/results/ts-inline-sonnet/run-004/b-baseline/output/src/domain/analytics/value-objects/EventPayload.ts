/** Value object representing the data payload of an analytics event. */
export interface EventPayload {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
