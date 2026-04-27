import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** PaymentMethod value object describing a customer's payment instrument. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
