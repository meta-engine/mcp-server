/** Value object describing a notification delivery attempt. */
export interface DeliveryAttempt {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
