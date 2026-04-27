import { Money } from "../../shared/value-objects/Money";
import { PaymentStatus } from "../enums/PaymentStatus";

/** A payment recorded against an Invoice. */
export interface Payment {
  amount: Money;
  status: PaymentStatus;
}
