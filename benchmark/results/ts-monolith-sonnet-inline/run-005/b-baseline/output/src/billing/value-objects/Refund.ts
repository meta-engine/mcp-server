import { Money } from '../../shared/value-objects/Money';
import { RefundReason } from '../enums/RefundReason';

/** Refund transaction with the reason for return. */
export interface Refund {
  amount: Money;
  reason: RefundReason;
}
