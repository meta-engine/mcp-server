import { EmailTemplate } from '../value-objects/email-template';
import { Id } from '../../shared/value-objects/id';

export class DeliveryDispatcher {

  create(input: Partial<EmailTemplate>): EmailTemplate { throw new Error('not implemented'); }

  findById(id: Id): EmailTemplate | null { throw new Error('not implemented'); }

  list(limit: number): EmailTemplate[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
