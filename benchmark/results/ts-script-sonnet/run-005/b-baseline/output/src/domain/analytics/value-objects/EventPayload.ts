/** Value object representing the data payload attached to an analytics event. */
export interface EventPayload {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
