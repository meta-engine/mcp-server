/** Value object representing the data payload carried by an analytics event. */
export interface EventPayload {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
