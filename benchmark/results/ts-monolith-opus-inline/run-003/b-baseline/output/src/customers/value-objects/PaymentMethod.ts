import { PaymentMethodKind } from "../enums/PaymentMethodKind";

/** Payment method on file for a customer. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
