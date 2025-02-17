import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
} from "@heroui/react";

interface UpdateNotificationProps {
  isOpen: boolean;
  onClose: () => void;
  version: string;
  releaseNotes: string;
  downloadUrl: string;
}

export default function UpdateNotification({
  isOpen,
  onClose,
  version,
  releaseNotes,
  downloadUrl,
}: UpdateNotificationProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalContent>
        <ModalHeader>New Version Available! 🚀</ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            <p className="text-lg font-medium">
              Version {version} is now available
            </p>
            <div className="bg-default-100 p-4 rounded-lg">
              <h4 className="font-medium mb-2">What&apos;s New:</h4>
              <div className="prose prose-sm">
                {releaseNotes.split("\n").map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button color="default" variant="light" onPress={onClose}>
            Later
          </Button>
          <Button
            color="primary"
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            Download Update
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
