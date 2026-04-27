import { PaymentMethodKind } from '../enums/payment-method-kind.enum';

/** PaymentMethod value object. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
