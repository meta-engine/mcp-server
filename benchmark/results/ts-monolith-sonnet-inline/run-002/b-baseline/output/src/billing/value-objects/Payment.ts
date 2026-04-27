import { Money } from '../../shared/value-objects/Money';
import { PaymentStatus } from '../enums/PaymentStatus';

/** Payment attempt record. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
