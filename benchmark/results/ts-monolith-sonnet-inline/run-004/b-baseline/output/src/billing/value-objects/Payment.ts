import { Money } from '../../shared/value-objects/Money';
import { PaymentStatus } from '../enums/PaymentStatus';

/** Payment transaction value object */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
