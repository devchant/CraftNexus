import { FaTimes } from "react-icons/fa";
const wallets = [
  { name: "MetaMask" },
  { name: "WalletConnect" },
  { name: "Coinbase Wallet", icon: "/wallets/coinbase.svg" },
  { name: "Phantom" },
];
export const ConnectWalletModal = ({
  isOpen,
  handleClose,
}: {
  isOpen: boolean;
  handleClose: () => void;
}) => {
  return !isOpen ? null : (
    <div className="fixed inset-0 bg-[rgba(0,0,0,.5)] backdrop-blur-[4px] bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Connect Wallet</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 cursor-pointer"
          >
            <FaTimes className="text-xl" />
          </button>
        </div>

        <div className="space-y-3">
          {wallets.map((wallet) => (
            <button
              key={wallet.name}
              className="flex items-center gap-4 w-full p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              onClick={() => {
                // Handle wallet connection here
                console.log(`Connecting to ${wallet.name}`);
                handleClose();
              }}
            >
              <span className="font-medium">{wallet.name}</span>
            </button>
          ))}
        </div>

        <p className="text-sm text-gray-500 mt-4 text-center">
          By connecting a wallet, you agree to our Terms of Service and Privacy
          Policy
        </p>
      </div>
    </div>
  );
};
