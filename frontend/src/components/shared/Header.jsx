import { Link } from "react-router-dom"

const Header = () => {
    return (
        <nav className="w-full bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white p-4 shadow-lg">
            <div className="max-w-6xl mx-auto flex justify-between items-center">
                <h1 className="text-2xl font-extrabold tracking-wide text-blue-400">
                    RealChat
                </h1>
                <ul className="flex space-x-6 text-lg font-medium">
                    <li>
                        <Link
                            to="/"
                            className="hover:text-blue-400 transition-all duration-300 hover:scale-105"
                        >
                            Home
                        </Link>
                    </li>
                    <li>
                        <Link
                            to="/editor"
                            className="hover:text-blue-400 transition-all duration-300 hover:scale-105"
                        >
                            Editor
                        </Link>
                    </li>
                    <li>
                        <Link
                            to="/knowledge"
                            className="hover:text-blue-400 transition-all duration-300 hover:scale-105"
                        >
                            Knowledge
                        </Link>
                    </li>
                </ul>
            </div>
        </nav>
    )
}


export default Header


