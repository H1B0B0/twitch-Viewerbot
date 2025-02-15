"use client";
import { Form, Input, Button, Card, CardHeader, CardBody } from "@heroui/react";
import { toast, ToastContainer } from "react-toastify";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "../functions/UserAPI";
import { RegisterData } from "../types/User";

export default function RegisterPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleRegister(formData: FormData) {
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirmPassword") as string;

    if (password !== confirmPassword) {
      toast.error("Passwords do not match", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      return;
    }

    const registerData: RegisterData = {
      username: formData.get("username") as string,
      TwitchUsername: formData.get("twitch username") as string,
      email: formData.get("email") as string,
      password: password,
    };

    try {
      setIsLoading(true);
      await register(registerData);
      toast.success("Account created successfully!", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      router.push("/login");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
      toast.error(errorMessage, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <ToastContainer />
      <Card className="space-y-8 p-8 w-96 md:w-[500px]">
        <CardHeader className="flex flex-col space-y-5">
          <h2 className="text-3xl font-extrabold text-center">
            Create Account
          </h2>
        </CardHeader>
        <Form className="mt-8 space-y-6" action={handleRegister}>
          <CardBody className="space-y-6">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-100 rounded-lg">
                {error}
              </div>
            )}
            <div>
              <Input type="text" name="username" label="Username" required />
            </div>
            <div>
              <Input type="email" name="email" label="Email" required />
            </div>
            <div>
              <Input
                type="text"
                name="twitch username"
                label="Twitch Username"
                required
              />
            </div>
            <div>
              <Input
                type="password"
                name="password"
                label="Password"
                required
              />
            </div>
            <div>
              <Input
                type="password"
                name="confirmPassword"
                label="Confirm Password"
                required
              />
            </div>
            <div>
              <Button
                type="submit"
                isLoading={isLoading}
                spinner={
                  <svg
                    className="animate-spin h-5 w-5 text-current"
                    fill="none"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      fill="currentColor"
                    />
                  </svg>
                }
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                {isLoading ? "Creating Account..." : "Create Account"}
              </Button>
              <div className="mt-4 text-center">
                <span className="text-sm text-gray-600">
                  Already have an account?{" "}
                </span>
                <Button
                  variant="ghost"
                  className="text-sm text-blue-600 hover:text-blue-800"
                  onPress={() => router.push("/login")}
                >
                  Login now
                </Button>
              </div>
            </div>
          </CardBody>
        </Form>
      </Card>
    </div>
  );
}
