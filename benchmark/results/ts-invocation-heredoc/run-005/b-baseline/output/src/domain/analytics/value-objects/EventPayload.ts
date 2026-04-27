/** Value object representing the payload carried by an analytics event. */
export interface EventPayload {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
