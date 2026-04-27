import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Stored payment method with kind and masked card digits. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
