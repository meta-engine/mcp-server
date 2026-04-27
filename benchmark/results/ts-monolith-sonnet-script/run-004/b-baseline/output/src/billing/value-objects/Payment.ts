import { Money } from '../../shared/value-objects/Money';
import { PaymentStatus } from '../enums/PaymentStatus';

/** Payment value object representing a payment transaction. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
