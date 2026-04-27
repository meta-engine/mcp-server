import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Customer payment method on file */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
