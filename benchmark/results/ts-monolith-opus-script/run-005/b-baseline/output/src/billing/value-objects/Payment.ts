import { Money } from "../../shared/value-objects/Money";
import { PaymentStatus } from "../enums/PaymentStatus";

/** Recorded payment against an invoice. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
