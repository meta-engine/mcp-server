import { Money } from '../../shared/value-objects/money';
import { PaymentStatus } from '../enums/payment-status.enum';

/** Payment value object. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
