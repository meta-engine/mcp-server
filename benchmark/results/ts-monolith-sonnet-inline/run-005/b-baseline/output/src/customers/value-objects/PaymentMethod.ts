import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Customer payment method with masked card digits. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
