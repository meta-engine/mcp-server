/** DeliveryAttempt value object representing a single attempt to deliver a notification. */
export interface DeliveryAttempt {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
