import { Money } from '../../shared/value-objects/Money';
import { RefundReason } from '../enums/RefundReason';

/** Refund issued against a billing transaction. */
export interface Refund {
  amount: Money;
  reason: RefundReason;
}
