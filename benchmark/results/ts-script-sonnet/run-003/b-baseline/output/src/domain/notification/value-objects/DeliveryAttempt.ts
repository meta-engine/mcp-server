/** Value object recording a single delivery attempt for a notification. */
export interface DeliveryAttempt {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
