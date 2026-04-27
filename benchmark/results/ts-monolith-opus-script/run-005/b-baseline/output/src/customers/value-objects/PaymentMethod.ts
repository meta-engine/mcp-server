import { PaymentMethodKind } from "../enums/PaymentMethodKind";

/** Customer-owned payment instrument descriptor. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
