import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** PaymentMethod value object. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
