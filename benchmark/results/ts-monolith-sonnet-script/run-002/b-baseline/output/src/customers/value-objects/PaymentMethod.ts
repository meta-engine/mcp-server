import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Payment method stored on a customer profile. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
