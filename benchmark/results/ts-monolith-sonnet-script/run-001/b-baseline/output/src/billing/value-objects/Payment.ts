import { Money } from '../../shared/value-objects/Money';
import { PaymentStatus } from '../enums/PaymentStatus';

/** A payment transaction record. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
