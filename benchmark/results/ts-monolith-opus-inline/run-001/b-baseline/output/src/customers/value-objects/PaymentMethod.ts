import { PaymentMethodKind } from "../enums/PaymentMethodKind";

/** Stored payment instrument tied to a customer. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
