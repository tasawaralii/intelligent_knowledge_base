const ProfileAvatar = ({ name }: { name: string | undefined }) => {
    if(!name) return null
    return (
        <div className="flex items-center space-x-3">
            <div className="h-8 w-8 rounded-full bg-gray-500 text-white flex items-center justify-center">
                {name[0].toUpperCase()}
            </div>
        </div>
    );
};  

export default ProfileAvatar