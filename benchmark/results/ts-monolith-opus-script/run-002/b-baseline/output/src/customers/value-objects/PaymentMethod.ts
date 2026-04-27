import { PaymentMethodKind } from "../enums/PaymentMethodKind";

/** Stored payment instrument metadata. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
