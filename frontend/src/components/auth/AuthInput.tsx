import React from "react";

interface AuthInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label: string;
    error?: string;
    touched?: boolean;
    successMessage?: string;
}

export default function AuthInput({
    label,
    error,
    touched,
    successMessage,
    className = "",
    ...props
}: AuthInputProps) {
    const hasValue = props.value && String(props.value).length > 0;
    const showError = touched && error && hasValue;

    return (
        <div>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <label className="block text-m font-medium">{label}</label>
                    {touched && !error && <span className="text-[#42BCEB]">✓</span>}
                </div>
                <div>
                    {showError && (
                        <span className="text-[0.75rem] text-red-500">{error}</span>
                    )}
                    {touched && !error && successMessage && (
                        <span className="text-[0.75rem] text-[#42BCEB]">{successMessage}</span>
                    )}
                </div>
            </div>
            <input
                {...props}
                className={`w-full py-[0.75rem] pl-[0.9375rem] pr-[1.25rem] border rounded-[0.3125rem] focus:outline-none ${showError ? "border-red-300" : "border-[#42BCEB]"
                    } ${className}`}
            />
        </div>
    );
}
