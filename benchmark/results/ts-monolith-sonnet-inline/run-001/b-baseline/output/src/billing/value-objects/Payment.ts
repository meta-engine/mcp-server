import { Money } from '../../shared/value-objects/Money';
import { PaymentStatus } from '../enums/PaymentStatus';

/** Represents a payment transaction. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
