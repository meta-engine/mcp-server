import { Money } from "../../shared/value-objects/Money";
import { PaymentStatus } from "../enums/PaymentStatus";

/** A captured payment against an invoice. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
