import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Represents a payment instrument on file. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
