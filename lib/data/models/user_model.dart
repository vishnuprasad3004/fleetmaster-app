class UserModel {
  UserModel({
    required this.id,
    required this.email,
    required this.username,
    required this.fullName,
    this.firstName,
    this.lastName,
    this.phoneNumber,
  });

  final String id;
  final String email;
  final String username;
  final String fullName;
  final String? firstName;
  final String? lastName;
  final String? phoneNumber;

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      email: json['email'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String? ?? json['username'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      phoneNumber: json['phone_number'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'username': username,
        'full_name': fullName,
        'first_name': firstName,
        'last_name': lastName,
        'phone_number': phoneNumber,
      };
}

class AuthSession {
  AuthSession({required this.user, required this.accessToken, required this.refreshToken});

  final UserModel user;
  final String accessToken;
  final String refreshToken;

  factory AuthSession.fromLoginData(Map<String, dynamic> data) {
    return AuthSession(
      user: UserModel.fromJson(data['user'] as Map<String, dynamic>),
      accessToken: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String,
    );
  }
}
