import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Customer's stored payment method. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
