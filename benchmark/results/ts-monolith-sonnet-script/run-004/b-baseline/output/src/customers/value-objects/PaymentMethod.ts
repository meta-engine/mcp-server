import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** PaymentMethod value object representing a customer payment instrument. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
