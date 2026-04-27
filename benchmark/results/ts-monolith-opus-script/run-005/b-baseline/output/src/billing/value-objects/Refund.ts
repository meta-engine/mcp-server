import { Money } from "../../shared/value-objects/Money";
import { RefundReason } from "../enums/RefundReason";

/** A refund issued against an invoice. */
export interface Refund {
  amount: Money;
  reason: RefundReason;
}
