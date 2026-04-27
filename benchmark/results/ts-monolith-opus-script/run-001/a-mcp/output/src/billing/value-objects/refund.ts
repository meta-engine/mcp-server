import { Money } from '../../shared/value-objects/money';
import { RefundReason } from '../enums/refund-reason.enum';

export interface Refund {
  amount: Money;
  reason: RefundReason;
}
