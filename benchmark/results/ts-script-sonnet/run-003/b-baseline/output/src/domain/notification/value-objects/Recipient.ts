/** Value object representing the intended recipient of a notification. */
export interface Recipient {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
