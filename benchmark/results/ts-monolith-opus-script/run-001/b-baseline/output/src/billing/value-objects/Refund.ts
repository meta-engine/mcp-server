import { Money } from '../../shared/value-objects/Money';
import { RefundReason } from '../enums/RefundReason';

/** Refund value object describing a refund issued against an invoice. */
export interface Refund {
  amount: Money;
  reason: RefundReason;
}
