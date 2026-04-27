import { Money } from '../../shared/value-objects/Money';
import { PaymentStatus } from '../enums/PaymentStatus';

/** A payment attempt associated with an invoice. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
