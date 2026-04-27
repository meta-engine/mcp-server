import { Money } from '../../shared/value-objects/money';
import { RefundReason } from '../enums/refund-reason.enum';

/** Refund value object. */
export interface Refund {
  amount: Money;
  reason: RefundReason;
}
