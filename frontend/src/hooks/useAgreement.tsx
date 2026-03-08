import { useState } from "react";

export interface AgreementState {
  all: boolean;
  terms: boolean;
  privacy: boolean;
  email: boolean;
  sns: boolean;
  push: boolean;
}

export function useAgreement() {
  const [agreements, setAgreements] = useState<AgreementState>({
    all: false,
    terms: false,
    privacy: false,
    email: false,
    sns: false,
    push: false,
  });

  const handleAllAgree = (checked: boolean) => {
    setAgreements({
      all: checked,
      terms: checked,
      privacy: checked,
      email: checked,
      sns: checked,
      push: checked,
    });
  };

  const updateAgreement = (key: keyof AgreementState, checked: boolean) => {
    setAgreements((prev) => {
      const updated = { ...prev, [key]: checked };
      const allChecked =
        updated.terms &&
        updated.privacy &&
        updated.email &&
        updated.sns &&
        updated.push;
      return { ...updated, all: allChecked };
    });
  };

  return { agreements, handleAllAgree, updateAgreement };
}