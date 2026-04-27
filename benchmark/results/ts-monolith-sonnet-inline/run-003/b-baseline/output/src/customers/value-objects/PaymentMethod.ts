import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** A customer's stored payment method. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
